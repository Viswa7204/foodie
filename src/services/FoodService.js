import axios from 'axios';
import { ApiContants } from '../contants';
import { getToken } from '../Store';
import { authHeader } from '../utils/Generator';

const getOneFoodById = async foodId => {
  console.log(`FoodService | getOneFoodById`);
  try {
    let foodResponse = await axios.get(
      `${ApiContants.BACKEND_API.BASE_API_URL}${ApiContants.BACKEND_API.FOOD}/${foodId}`,
      {
        headers: authHeader(getToken()),
      },
    );
    if (foodResponse?.status === 200) {
      return {
        status: true,
        message: `Food data fetched`,
        data: foodResponse?.data?.data,
      };
    } else {
      return {
        status: false,
        message: `Food data not found`,
      };
    }
  } catch (error) {
    return {
      status: false,
      message: `Food data not found`,
    };
  }
};

export default {getOneFoodById};
